/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Components
import App from "./App.vue";
import AppFrame from "./components/AppFrame.vue";
import TileButton from "./components/TileButton.vue";

// Composables
import { createApp } from "vue";

// Plugins
import { registerPlugins } from "@/plugins";

const app = createApp(App);

registerPlugins(app);

app.component("TileButton", TileButton).component("AppFrame", AppFrame).mount("#app");
