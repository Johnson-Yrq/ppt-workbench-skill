"""Offline regression for the image-API generator: the network layer is replaced by a fake."""
import base64
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse

import generate_images as gi
from common import ASSETS, image_size, placeholder_png, read_raster
from prepare_images import prepare


class FakeTransport:
    """Records every request and answers like the real providers would."""

    def __init__(self, image=None, fail_first=0, status=200):
        self.calls, self.image, self.fail_first, self.status = [], image or placeholder_png(1536, 1024), fail_first, status

    def __call__(self, method, url, headers, body=None, timeout=180):
        self.calls.append({'method': method, 'url': url, 'headers': dict(headers), 'body': body, 'timeout': timeout})
        if self.fail_first:
            self.fail_first -= 1
            return 429, {}, b'{"error": {"message": "rate limited"}}'
        if self.status != 200:
            return self.status, {}, b'{"error": {"message": "nope"}}'
        path = urlparse(url).path
        if path.endswith('/models'):
            return 200, {}, json.dumps({'data': [{'id': 'gpt-image-1'}]}).encode()
        if path.endswith(':generateContent'):
            return 200, {}, json.dumps({'candidates': [{'content': {'parts': [{'text': 'ok'}, {'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(self.image).decode()}}]}}]}).encode()
        return 200, {}, json.dumps({'data': [{'b64_json': base64.b64encode(self.image).decode()}]}).encode()


class GenerateImages(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='generate-images-')
        self.root = Path(self.tmp.name)
        deck = json.loads((ASSETS / 'deck.example.json').read_text(encoding='utf-8'))
        (self.root / 'deck.json').write_text(json.dumps(deck, ensure_ascii=False), encoding='utf-8')
        self.deck = deck
        self.handoff = self.root / 'image-handoff'
        with contextlib.redirect_stdout(io.StringIO()):
            prepare(str(self.root / 'deck.json'), str(self.handoff))
        self.config = self.root / 'image-api.json'
        self.config.write_text(json.dumps({'provider': 'openai', 'url': 'https://example.test/v1/', 'model': 'gpt-image-1', 'api_key': 'sk-test-1234567890'}), encoding='utf-8')
        self.env = dict(os.environ)
        for name in list(gi.ENV.values()) + [gi.CONFIG_ENV, 'OPENAI_API_KEY', 'GEMINI_API_KEY']:
            os.environ.pop(name, None)
        os.environ[gi.CONFIG_ENV] = str(self.config)
        self.original_http = gi.http_request

    def tearDown(self):
        gi.http_request = self.original_http
        os.environ.clear(); os.environ.update(self.env)
        self.tmp.cleanup()

    def run_cli(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return gi.main(list(argv))

    def manifest(self):
        return json.loads((self.handoff / 'image-manifest.json').read_text(encoding='utf-8'))

    def test_settings_precedence_and_key_sources(self):
        args = gi.main.__globals__['argparse'].Namespace(config=None, provider=None, url=None, model=None, reference=None, fit=None, quality=None, timeout=None)
        s = gi.resolve_settings(args)
        self.assertEqual((s['provider'], s['url'], s['model'], s['api_key']), ('openai', 'https://example.test/v1', 'gpt-image-1', 'sk-test-1234567890'))
        self.assertIn('配置文件', s['api_key_source'])
        os.environ[gi.ENV['api_key']] = 'sk-env-0987654321'
        os.environ[gi.ENV['model']] = 'dall-e-3'
        s = gi.resolve_settings(args)
        self.assertEqual((s['model'], s['api_key']), ('dall-e-3', 'sk-env-0987654321'))
        self.assertEqual(gi.masked(s['api_key']), 'sk-…4321')
        # The provider's own variable is a fallback when nothing else names a key.
        self.config.write_text(json.dumps({'provider': 'gemini'}), encoding='utf-8')
        os.environ.pop(gi.ENV['api_key']); os.environ.pop(gi.ENV['model'])
        os.environ['GEMINI_API_KEY'] = 'AIza-fallback-key'
        s = gi.resolve_settings(args)
        self.assertEqual((s['provider'], s['url'], s['model'], s['api_key']), ('gemini', gi.PROVIDERS['gemini']['url'], gi.PROVIDERS['gemini']['model'], 'AIza-fallback-key'))
        # A pasted full endpoint is reduced to the base URL.
        self.assertEqual(gi.normalize_url('openai', 'https://proxy.test/v1/images/generations'), 'https://proxy.test/v1')
        self.assertEqual(gi.normalize_url('gemini', 'https://g.test/v1beta/models/x:generateContent'), 'https://g.test/v1beta')
        with self.assertRaises(ValueError):
            gi.normalize_url('openai', 'api.openai.com/v1')

    def test_setup_without_tty_never_stores_a_key_from_arguments(self):
        self.assertEqual(self.run_cli('--setup', '--provider', 'openai', '--url', 'https://proxy.test/v1/', '--model', 'gpt-image-1', '--no-key'), 0)
        stored = json.loads(self.config.read_text(encoding='utf-8'))
        self.assertEqual(stored, {'provider': 'openai', 'url': 'https://proxy.test/v1', 'model': 'gpt-image-1'})
        self.assertEqual(self.run_cli('--setup', '--key-env', 'MY_KEY'), 0)
        self.assertEqual(json.loads(self.config.read_text(encoding='utf-8'))['api_key_env'], 'MY_KEY')
        if os.name != 'nt':
            self.assertEqual(self.config.stat().st_mode & 0o777, 0o600)

    def test_sizes_and_reference_policy(self):
        base = {'sizes': {}, 'model': 'gpt-image-1', 'provider': 'openai', 'reference': 'auto'}
        self.assertEqual(gi.openai_size(base, '16:9'), '1536x1024')
        self.assertEqual(gi.openai_size(base, '3:4'), '1024x1536')
        self.assertEqual(gi.openai_size(dict(base, model='dall-e-3'), '4:3'), '1792x1024')
        self.assertEqual(gi.openai_size(dict(base, sizes={'4:3': '1024x768', 'landscape': '1280x720'}), '4:3'), '1024x768')
        self.assertEqual(gi.openai_size(dict(base, sizes={'landscape': '1280x720'}), '16:9'), '1280x720')
        self.assertEqual(gi.gemini_ratio('2:1'), '16:9')
        self.assertEqual(gi.gemini_ratio('3:1'), '21:9')
        self.assertEqual(gi.gemini_ratio('4:3'), '4:3')
        ref = self.handoff / 'style-reference.png'
        ref.write_bytes(placeholder_png(64, 64))
        self.assertTrue(gi.uses_reference(base, ref))
        self.assertFalse(gi.uses_reference(dict(base, model='dall-e-3'), ref))
        self.assertTrue(gi.uses_reference(dict(base, model='dall-e-3', reference='on'), ref))
        self.assertFalse(gi.uses_reference(dict(base, reference='off'), ref))
        self.assertFalse(gi.uses_reference(base, self.handoff / 'absent.png'))

    def test_dry_run_needs_no_key_and_calls_nothing(self):
        self.config.write_text(json.dumps({'provider': 'openai'}), encoding='utf-8')
        fake = FakeTransport(); gi.http_request = fake
        self.assertEqual(self.run_cli(str(self.root / 'deck.json'), '--dry-run'), 0)
        self.assertEqual(fake.calls, [])

    def test_generates_missing_images_pads_to_ratio_and_updates_manifest(self):
        fake = FakeTransport(); gi.http_request = fake
        missing_before = [e for e in self.manifest()['images'] if e['status'] == 'missing']
        self.assertTrue(missing_before)
        code = self.run_cli(str(self.root / 'deck.json'), '--pages', '1,2')
        self.assertEqual(code, 0)
        self.assertEqual(len(fake.calls), 2)
        call = fake.calls[0]
        self.assertEqual(call['url'], 'https://example.test/v1/images/generations')
        self.assertEqual(call['headers']['Authorization'], 'Bearer sk-test-1234567890')
        body = json.loads(call['body'])
        first = self.manifest()['images'][0]
        self.assertEqual((body['model'], body['n'], body['size']), ('gpt-image-1', 1, gi.openai_size({'sizes': {}, 'model': 'gpt-image-1'}, first['ratio'])))
        self.assertNotIn('response_format', body)
        self.assertIn('This page (describe the scene', body['prompt'])
        manifest = self.manifest()
        done = [e for e in manifest['images'] if e['page'] in (1, 2)]
        for entry in done:
            self.assertEqual(entry['status'], 'generated')
            self.assertEqual(entry['method'], 'api:openai/gpt-image-1')
            file = self.root / entry['file']
            mime, data = read_raster(file)
            w, h = image_size(mime, data)
            self.assertEqual(mime, 'image/png')
            self.assertAlmostEqual(w / h, gi.ratio_value(entry['ratio']), delta=0.01)
        self.assertEqual([e['status'] for e in manifest['images'] if e['page'] not in (1, 2)], ['missing'] * (len(manifest['images']) - len(done)))

    def test_force_keeps_previous_version_and_retries_rate_limits(self):
        fake = FakeTransport(fail_first=1); gi.http_request = fake
        gi.time.sleep = lambda s: None
        target = self.root / self.manifest()['images'][0]['file']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(placeholder_png(10, 10))
        self.assertEqual(self.run_cli(str(self.root / 'deck.json'), '--pages', '1', '--force'), 0)
        entry = self.manifest()['images'][0]
        self.assertEqual(entry['status'], 'generated')
        self.assertTrue((self.root / entry['previous_file']).is_file())
        self.assertEqual(len(fake.calls), 2)
        # Without --force an existing file is left alone and reported as provided.
        fake.calls.clear()
        self.assertEqual(self.run_cli(str(self.root / 'deck.json'), '--pages', '1'), 0)
        self.assertEqual(fake.calls, [])

    def test_auth_failure_stops_and_names_the_key(self):
        gi.http_request = FakeTransport(status=401)
        self.assertEqual(self.run_cli(str(self.root / 'deck.json'), '--pages', '1'), 1)
        self.assertEqual(self.manifest()['images'][0]['status'], 'missing')
        self.config.write_text(json.dumps({'provider': 'openai'}), encoding='utf-8')
        self.assertEqual(self.run_cli(str(self.root / 'deck.json'), '--pages', '1'), 1)
        self.assertEqual(self.run_cli('--check'), 1)

    def test_check_uses_the_free_models_endpoint(self):
        fake = FakeTransport(); gi.http_request = fake
        self.assertEqual(self.run_cli('--check'), 0)
        self.assertEqual(fake.calls[0]['url'], 'https://example.test/v1/models')
        gi.http_request = FakeTransport(status=404)
        self.assertEqual(self.run_cli('--check'), 0)  # unknown listing endpoint is a warning, not a failure

    def test_gemini_request_shape_and_reference(self):
        self.config.write_text(json.dumps({'provider': 'gemini', 'api_key': 'AIza-test-key-000000'}), encoding='utf-8')
        (self.handoff / 'style-reference.png').write_bytes(placeholder_png(32, 32))
        manifest = self.manifest(); manifest['style_reference'] = 'style-reference.png'
        (self.handoff / 'image-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
        fake = FakeTransport(image=placeholder_png(1344, 768)); gi.http_request = fake
        self.assertEqual(self.run_cli(str(self.root / 'deck.json'), '--pages', '2'), 0)
        call = fake.calls[0]
        self.assertTrue(call['url'].endswith('/models/gemini-2.5-flash-image:generateContent'))
        self.assertEqual(call['headers']['x-goog-api-key'], 'AIza-test-key-000000')
        body = json.loads(call['body'])
        parts = body['contents'][0]['parts']
        self.assertIn('inlineData', parts[0])
        self.assertEqual(body['generationConfig']['responseModalities'], ['TEXT', 'IMAGE'])
        self.assertIn(body['generationConfig']['imageConfig']['aspectRatio'], gi.GEMINI_RATIOS)
        entry = [e for e in self.manifest()['images'] if e['page'] == 2][0]
        self.assertEqual((entry['status'], entry['reference_used']), ('generated', True))

    def test_openai_edit_with_reference_uses_multipart(self):
        (self.handoff / 'style-reference.png').write_bytes(placeholder_png(32, 32))
        manifest = self.manifest(); manifest['style_reference'] = 'style-reference.png'
        (self.handoff / 'image-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
        fake = FakeTransport(); gi.http_request = fake
        self.assertEqual(self.run_cli(str(self.root / 'deck.json'), '--pages', '1'), 0)
        call = fake.calls[0]
        self.assertTrue(call['url'].endswith('/images/edits'))
        self.assertTrue(call['headers']['Content-Type'].startswith('multipart/form-data; boundary='))
        self.assertIn(b'name="image[]"; filename="style-reference.png"', call['body'])
        self.assertIn(b'name="model"\r\n\r\ngpt-image-1', call['body'])


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GenerateImages)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(run())
