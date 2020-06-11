<template>
  <button
    v-if="!collection.loadingNextPage"
    :class="{ primary: primary, secondary: !primary }"
    @click.prevent="appendToCollection"
  >
    Load More
  </button>
  <ComponentLoadingSVG v-else />
</template>

<script>
export default {
  name: 'LoadMoreButton',
  props: {
    primary: {
      type: Boolean,
      default: true,
    },
    collection: {
      required: true,
      type: Object,
    },
  },
  methods: {
    appendToCollection() {
      this.collection.addNextPage()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';

.primary {
  @include primary-button;
}

.secondary {
  @include secondary-button;
}
</style>
