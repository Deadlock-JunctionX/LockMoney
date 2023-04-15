// Utilities
import { defineStore } from "pinia";
import axios from "axios";
import Cookies from "js-cookie";

export const useAppStore = defineStore("app", {
  state: () => ({
    user: null,
  }),
  actions: {
    fetchUser() {
      return axios
        .get("/users/me/info", {
          headers: {
            Authorization: `Bearer ${Cookies.get("access_token")}`,
          },
        })
        .then((response) => {
          this.user = response.data;
        });
    },
  },
});
