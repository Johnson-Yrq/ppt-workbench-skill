/* Editable ratios: the table is the only source; saved HTML retains its values. */
(()=>{'use strict';
 function update(host){
  const cells=host.querySelector('.comp-progress-data tbody tr').cells;
  const values=[...cells].map(cell=>cell.textContent.trim()).map(raw=>raw===''?NaN:Number(raw));
  const [value,max]=values,valid=values.every(Number.isFinite)&&max>0&&value>=0&&value<=max;
  host.toggleAttribute('data-invalid',!valid);if(!valid)return;
  const percent=Number((value/max*100).toFixed(1)),track=host.querySelector('.comp-progress-track');
  host.querySelector('.comp-progress-fill').style.width=percent+'%';
  host.querySelector('.comp-progress-percent').textContent=percent+'%';
  track.setAttribute('aria-valuenow',value);track.setAttribute('aria-valuemax',max);
 }
 const refresh=()=>document.querySelectorAll('.comp-progress').forEach(update);
 document.addEventListener('input',event=>{const table=event.target.closest('.comp-progress-data');if(table)update(table.closest('.comp-progress'));});
 window.slideCompositions={refresh};refresh();
})();
