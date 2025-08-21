function cssVar(name){ return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }

function chartPalette(){
  // Tenta usar a cor "color" do :root (compatível com temas que mudam a cor do texto no body)
  const doc = document.documentElement;
  const text = getComputedStyle(doc).getPropertyValue('color').trim() || cssVar('--text') || '#e5e7eb';
  const grid = cssVar('--border') || 'rgba(255,255,255,.15)';
  const bg   = cssVar('--surface') || '#0b1222';
  const brand= cssVar('--brand-1') || text;
  const muted= cssVar('--muted') || text;
  return { text, grid, bg, brand, muted };
}

// util: aplica cor se o campo ainda não foi definido pelo dataset
function ensure(obj, path, value){
  const parts = path.split('.');
  let ref = obj;
  for (let i=0;i<parts.length-1;i++){
    ref[parts[i]] = ref[parts[i]] ?? {};
    ref = ref[parts[i]];
  }
  const last = parts[parts.length-1];
  if (ref[last] == null) ref[last] = value;
}

// util simples para dar transparência (funciona com rgb(a) ou hex #rrggbb)
function withAlpha(color, alpha){
  try{
    if (color.startsWith('#')){
      const r = parseInt(color.slice(1,3),16);
      const g = parseInt(color.slice(3,5),16);
      const b = parseInt(color.slice(5,7),16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    // rgb/rgba(...) -> força novo alpha
    const m = color.match(/rgba?\(([^)]+)\)/i);
    if (m){
      const [r,g,b] = m[1].split(',').map(s=>parseFloat(s));
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
  }catch(e){}
  return color; // fallback
}

function applyChartTheme(chart){
  const pal = chartPalette();

  // Defaults globais
  if (window.Chart?.defaults){
    Chart.defaults.color = pal.text;
    ensure(Chart.defaults, 'plugins.legend.labels.color', pal.text);
    ensure(Chart.defaults, 'plugins.title.color', pal.text);
    ensure(Chart.defaults, 'plugins.tooltip.titleColor', pal.text);
    ensure(Chart.defaults, 'plugins.tooltip.bodyColor', pal.text);
    ensure(Chart.defaults, 'plugins.tooltip.backgroundColor', withAlpha(pal.bg, .9));
  }

  // Eixos + grid
  if (chart.options?.scales){
    for (const axisKey of Object.keys(chart.options.scales)){
      const axis = chart.options.scales[axisKey] || {};
      ensure(axis, 'ticks.color', pal.text);
      // grid mais clara no dark para aparecer
      ensure(axis, 'grid.color', withAlpha(pal.grid, .5));
      chart.options.scales[axisKey] = axis;
    }
  }

  // Legend/Title por gráfico (caso defaults não peguem)
  if (chart.options?.plugins){
    ensure(chart.options, 'plugins.legend.labels.color', pal.text);
    ensure(chart.options, 'plugins.title.color', pal.text);
    ensure(chart.options, 'plugins.tooltip.titleColor', pal.text);
    ensure(chart.options, 'plugins.tooltip.bodyColor', pal.text);
    ensure(chart.options, 'plugins.tooltip.backgroundColor', withAlpha(pal.bg, .9));
  }

  // Datasets (fallbacks seguros)
  const type = chart.config?.type;
  const datasets = chart.data?.datasets || [];
  datasets.forEach((ds)=>{
    // Se o dataset já definiu cores, respeitamos.
    if (type === 'line' || ds.type === 'line'){
      ensure(ds, 'borderColor', pal.brand);
      ensure(ds, 'pointBackgroundColor', pal.brand);
      ensure(ds, 'pointBorderColor', pal.brand);
      // se for área (fill: true), fundo translúcido
      if (ds.fill) ensure(ds, 'backgroundColor', withAlpha(pal.brand, .15));
      ensure(ds, 'tension', 0.35);
    } else if (type === 'bar' || ds.type === 'bar'){
      ensure(ds, 'backgroundColor', withAlpha(pal.brand, .7));
      ensure(ds, 'borderColor', pal.brand);
      ensure(ds, 'borderWidth', 1);
    } else if (type === 'pie' || type === 'doughnut' || ds.type === 'pie' || ds.type === 'doughnut'){
      // Se não tiver cores, cria uma paleta baseada na brand/text
      if (!ds.backgroundColor){
        ds.backgroundColor = [
          withAlpha(pal.brand, .85),
          withAlpha(pal.text,  .65),
          withAlpha(pal.muted, .65),
          withAlpha(pal.grid,  .65),
        ];
      }
      ensure(ds, 'borderColor', withAlpha(pal.bg, 1));
      ensure(ds, 'borderWidth', 1);
    } else {
      // fallback genérico
      ensure(ds, 'borderColor', pal.brand);
      ensure(ds, 'backgroundColor', withAlpha(pal.brand, .15));
    }
  });

  chart.update('none');
}

// Inicializa tema nos gráficos existentes
window.addEventListener('load', () => {
  if (window.Chart && Chart.instances) {
    Object.values(Chart.instances).forEach((inst)=> applyChartTheme(inst));
  }
});

// Reaplica quando alternar o tema (mantém seu gancho)
(function(){
  const origToggle = window.toggleTheme;
  window.toggleTheme = function(){
    origToggle ? origToggle() : null;
    setTimeout(()=>{
      if (window.Chart && Chart.instances) {
        Object.values(Chart.instances).forEach((inst)=> applyChartTheme(inst));
      }
    }, 60);
  };
})();
