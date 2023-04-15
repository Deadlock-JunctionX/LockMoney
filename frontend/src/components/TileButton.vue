<template>
  <div>
    <a class="link-wrapper" :href="href">
      <div class="text-center">
        <v-icon :color="color" size="48">{{ icon }}</v-icon>

        <p class="text-caption">
          {{ text }}
        </p>
      </div>
    </a>
  </div>
</template>

<script>
export default {
  props: {
    href: {
      default: "#",
      type: String,
    },
    icon: {
      default: "",
      type: String,
    },
    text: {
      default: "",
      type: String,
    },
    color: {
      default: "",
      type: String,
    }
  }
}
</script>

<style scoped>
.link-wrapper {
  text-decoration: none;
  color: inherit;
  background-color: none;
  all: unset;
}

</style>
