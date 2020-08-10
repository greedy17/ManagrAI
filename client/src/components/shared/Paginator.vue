<template>
  <div class="paginator-container">
    <ComponentLoadingSVG v-if="loading" color="main-gray" />
    <!-- PB Current implementation is only show more -->
    <button v-if="!loading" class="btn-load" @click="$emit('next-page')" :unbordered="true">
      <span>
        <svg
          width="15px"
          height="15px"
          class="btn-load__icon"
          :class="{ horizontal: orientation == 'horizontal' }"
          viewBox="0 0 24 24"
        >
          <use xlink:href="@/assets/images/svg-repo.svg#caret" />
        </svg>
      </span>
    </button>
  </div>
</template>

<script>
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'
export default {
  name: 'Paginator',
  components: {
    ComponentLoadingSVG,
  },
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    /* NIP 6/24/20 Following parameters are still under construction, and only to be used in conjunction with PaginatorBack */
    currentPage: {
      type: [String, Number],
      required: false,
    },
    nextPage: {
      type: Boolean,
      default: false,
    },
    orientation: {
      type: String,
      default: 'vertical',
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
.paginator-container {
  width: 100%;
}
button {
  outline: none;
  border: none;
}
.btn-load {
  width: 100%;
  background-color: transparent;
  &__icon {
    fill: gray;
    transform: rotate(90deg);
    &:hover {
      fill: $dark-green;
    }
  }
  &__icon.horizontal {
    transform: rotate(-90deg);
  }
}
</style>
