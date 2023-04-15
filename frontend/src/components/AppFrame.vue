<template>
  <div>
    <slot></slot>

    <v-bottom-navigation elevation="8" grow density="comfortable" :height="64" color="primary">
      <v-btn to="/transactions">
        <v-icon size="x-large">mdi-view-list</v-icon>
        Giao dịch
      </v-btn>
      <v-btn to="/home">
        <v-icon size="xx-large">mdi-home-circle</v-icon>
      </v-btn>
      <v-btn to="/settings">
        <v-icon size="x-large">mdi-account</v-icon>
        Cài đặt
      </v-btn>
    </v-bottom-navigation>
  </div>
</template>

<script>
export default {

}
</script>
