/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */
import axios from "axios";

// Components
import App from "./App.vue";
import AppFrame from "./components/AppFrame.vue";
import TileButton from "./components/TileButton.vue";
import router from "./router";
import VueCookies from 'vue3-cookies'
import Cookies from "js-cookie"


// Composables
import { createApp } from "vue";

// Plugins
import { registerPlugins } from "@/plugins";

const app = createApp(App);
app.use(VueCookies);

registerPlugins(app);
router.app = app;

app.component("TileButton", TileButton).component("AppFrame", AppFrame).mount("#app");

axios.defaults.baseURL = import.meta.env.VITE_API_ROOT
axios.defaults.headers.Authorization = `Bearer ${Cookies.get("access_token")}`
