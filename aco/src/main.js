import './assets/main.css'
import { createMemoryHistory, createRouter } from 'vue-router'

import { createApp } from 'vue'
import App from './App.vue'
import NotFound from './NotFound.vue'

const routes = [
    { path: '/', component: App },
    { path: '/NotFound', component: NotFound },
];

const router = createRouter({
    history: createMemoryHistory(),
    routes,
});

if (window.location.pathname !== '/') { // Bad Solution but it works
    createApp(NotFound)
      .use(router)
      .mount('#app');
} else {
    createApp(App)
      .use(router)
      .mount('#app');
}
