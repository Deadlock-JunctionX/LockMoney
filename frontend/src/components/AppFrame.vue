<template>
  <div>
    <slot></slot>

    <v-bottom-navigation bg-color="primary">
      <v-btn href="/transactions">
        <v-icon>mdi-view-list</v-icon>
        Giao dịch
      </v-btn>
      <v-btn href="/">
        <v-icon>mdi-home</v-icon>
        Màn hình chính
      </v-btn>
      <v-btn href="/settings">
        <v-icon>mdi-account</v-icon>
        Cài đặt
      </v-btn>
    </v-bottom-navigation>
  </div>
</template>

<script>
export default {

}
</script>
