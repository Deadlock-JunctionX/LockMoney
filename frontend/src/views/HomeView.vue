<template>
  <AppFrame>
    <!-- Top banner -->
    <div class="banner-bg d-flex justify-center align-center">
      <!-- Balance display -->
      <v-card flat rounded class="banner-inner" density="compact">
        <v-card-text class="text-right text-caption">
          Xin chào, <b>{{ user.name }}</b>
        </v-card-text>
        <v-card-text class="mt-n4 text-left"> Tài khoản 1 </v-card-text>

        <v-card-text class="mt-n6 text-left text-h5">
          10,000,000 VND
        </v-card-text>
      </v-card>
    </div>

    <v-container>
      <v-row class="py-2 px-2">
        <div style="width: 100%" class="d-flex justify-space-between px-2">
          <TileButton
            href="/transfer"
            icon="mdi-cash-multiple"
            text="Chuyển tiền"
            color="#81afde"
          ></TileButton>

          <TileButton
            icon="mdi-qrcode"
            text="Scan QR"
            color="#f0cd51"
          ></TileButton>

          <TileButton
            icon="mdi-wallet"
            text="Nạp/Rút tiền"
            color="#f78539"
          ></TileButton>

          <TileButton
            icon="mdi-credit-card"
            text="Thanh toán"
            color="#7bff61"
          ></TileButton>
        </div>
      </v-row>
    </v-container>
  </AppFrame>
</template>

<script>
import adImage from "../assets/junctionx.jpg";
import { useAppStore } from "../store/app.js";

const store = useAppStore();

export default {
  computed: {
    adImage() {
      return adImage
    },
    user() {
      return store.user;
    }
  },
};
</script>

<style scoped>
.banner-bg {
  height: 30vh;
  background: rgb(57, 117, 185);
  background: linear-gradient(
    27deg,
    rgba(57, 117, 185, 1) 15%,
    rgba(105, 80, 190, 1) 46%,
    rgba(150, 103, 187, 1) 78%
  );
}

.banner-inner {
  width: 80vw;
}
</style>
