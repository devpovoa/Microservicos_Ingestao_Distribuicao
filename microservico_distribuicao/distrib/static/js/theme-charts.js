function cssVar(name){ return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
function chartPalette(){
  return {
    text: getComputedStyle(document.documentElement).getPropertyValue('color').trim() || cssVar('--text'),
    grid: cssVar('--border'),
    bg: cssVar('--surface'),
  };
}
function applyChartTheme(chart){
  const pal = chartPalette();
  chart.options.scales.x.ticks.color = pal.text;
  chart.options.scales.y.ticks.color = pal.text;
  chart.options.scales.x.grid.color  = pal.grid;
  chart.options.scales.y.grid.color  = pal.grid;
  if (chart.options.plugins?.legend) chart.options.plugins.legend.labels.color = pal.text;
  chart.update('none');
}
// Inicializa tema nos gráficos existentes
window.addEventListener('load', () => {
  if (window.Chart && Chart.instances) {
    Object.values(Chart.instances).forEach((inst)=> applyChartTheme(inst));
  }
});
// Reaplica quando alternar o tema
(function(){
  const origToggle = window.toggleTheme;
  window.toggleTheme = function(){
    origToggle ? origToggle() : null;
    // aguarda CSS aplicar e retematiza
    setTimeout(()=>{
      if (window.Chart && Chart.instances) {
        Object.values(Chart.instances).forEach((inst)=> applyChartTheme(inst));
      }
    }, 50);
  };
})();

