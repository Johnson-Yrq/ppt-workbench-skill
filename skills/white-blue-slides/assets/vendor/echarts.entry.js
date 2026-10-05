/* Entry for the trimmed echarts.min.js: only what charts.js renders (bar, line, pie/donut as SVG).
 * Rebuild after adding a chart type or component (echarts@5.6.0, zrender@5.6.1, esbuild):
 *   npx esbuild echarts.entry.js --bundle --minify --format=iife --global-name=echarts --legal-comments=inline --outfile=out.js
 * then write echarts.min.js as the Apache license comment at the top of the current file followed by out.js. */
import {use} from 'echarts/core';
import {BarChart, LineChart, PieChart} from 'echarts/charts';
import {AriaComponent, GridComponent, LegendComponent, TitleComponent, TooltipComponent} from 'echarts/components';
import {SVGRenderer} from 'echarts/renderers';
use([BarChart, LineChart, PieChart, AriaComponent, GridComponent, LegendComponent, TitleComponent, TooltipComponent, SVGRenderer]);
export * from 'echarts/core';
