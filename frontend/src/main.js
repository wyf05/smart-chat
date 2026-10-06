import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 拟物字体三件套（showcase 同款，本地打包离线可用）
import '@fontsource/playfair-display/700.css'
import '@fontsource/playfair-display/900.css'
import '@fontsource/albert-sans/400.css'
import '@fontsource/albert-sans/600.css'
import '@fontsource/albert-sans/700.css'
import '@fontsource/fragment-mono/400.css'
import './styles/skeuo.css'   // 拟物设计（Skeuomorphism）全局主题
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
