const sharp=require('C:/Users/26079/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const path=require('path');
async function main(){
 for(const n of ['MCU_IO','MCU_PWR']){
  const p=path.join(__dirname,'after_svg','XWatch_Rev3.0-'+n+'.svg');
  await sharp(p,{density:180}).flatten({background:'#ffffff'}).png().toFile(path.join(__dirname,n+'_verified.png'));
 }
 await sharp(path.join(__dirname,'footprint_svg','STM32U5A9BJY6QTR.svg'),{density:1800}).flatten({background:'#ffffff'}).resize({width:1600}).png().toFile(path.join(__dirname,'footprint_verified.png'));
}
main().catch(e=>{console.error(e.message);process.exit(1)});
