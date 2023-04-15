<template>
  <div style="height: 100%" class="d-flex justify-center align-center">
    <v-card width="90%">
      <v-card-title>
        Đăng nhập
      </v-card-title>

      <v-card-text>
        <v-text-field
          label="Số điện thoại"
          type="tel"
          variant="outlined"
          placeholder="0912345678"
          dense
          v-model="loginForm.phone"
        ></v-text-field>

        <v-text-field
          label="Mật khẩu"
          type="password"
          variant="outlined"
          dense
          v-model="loginForm.password"
          @keyup.enter="login"
        ></v-text-field>

        <v-btn :loading="loading" color="success" block @click="login">
          Đăng nhập
        </v-btn>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import axios from 'axios';
import Cookies from 'js-cookie'

export default {
  data() {
    return {
      loginForm: {
        phone: "",
        password: "",
      },
      loading: false
    }
  },
  methods: {
    login() {
      this.loading = true;

      return axios.post("/login", this.loginForm)
        .then((response) => {
          const token = response.data.token;
          Cookies.set("access_token", token);
          axios.defaults.headers.Authorization = `Bearer ${Cookies.get("access_token")}`

          if (this.$route.query.redirect) {
            this.$router.push(this.$route.query.redirect)
          }
        })
        .catch(() => {
          alert("Mật khẩu hoặc SĐT không đúng")
        })
        .finally(() => {
          this.loading = false;
        })
    }
  },
}
</script>
