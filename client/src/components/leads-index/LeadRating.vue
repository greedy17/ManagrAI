<template>
  <div class="rating" :class="{ active: isActive }" @click="onRatingClick(rating)">
    <span v-for="n in 5" :key="n" class="icon-container">
      <img v-if="n <= rating" src="@/assets/images/star.svg" alt="star filled" />
      <img v-else src="@/assets/images/star_outline.svg" alt="star outline" />
    </span>
  </div>
</template>

<script>
export default {
  name: 'LeadRating',
  props: {
    rating: {
      type: Number,
      required: true,
    },
    isActive: {
      type: Boolean,
    },
  },
  methods: {
    onRatingClick(rating) {
      this.$emit('update-rating-filter', rating)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/utils';

.rating {
  @include pointer-on-hover();
  border: 2px solid rgba($color: $dark-green, $alpha: 0);
  width: 7rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  opacity: 0.4;
  display: flex;
  flex-flow: row;
  align-items: center;

  .label {
    font-size: 0.8rem;
    margin-right: 0.75rem;
  }
}

.active {
  border: 2px solid rgba($color: $dark-green, $alpha: 1);
}
</style>
