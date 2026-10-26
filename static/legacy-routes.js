'use strict';
(()=>{
const path=location.pathname.replace(/\/index\.html$/, '/').replace(/\/$/, '');
const year=path.match(/^\/(publications|news)(\d{4})$/);
const aliases={'/all':'/publications/all/','/covers':'/publications/covers/','/selected-publications':'/publications/selected/','/microrobot':'/publications/microrobot/','/news-all':'/news/all/'};
const target=year?'/'+year[1]+'/'+year[2]+'/':aliases[path];
if(target)location.replace(target+location.search+location.hash);
})();
