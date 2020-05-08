<template>
  <div class="rating">
    <span v-if="label" class="label">Rating</span>
    <span v-for="n in 5" :key="n" class="icon-container">
      <img
        v-if="n <= rating"
        src="@/assets/images/star.svg"
        alt="star filled"
        @click="onRatingClick(n)"
      />
      <img
        v-else
        src="@/assets/images/star_outline.svg"
        alt="star outline"
        @click="onRatingClick(n)"
      />
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
    label: {
      type: Boolean,
    },
  },
  methods: {
    onRatingClick(rating) {
      this.$emit('updated-rating', rating)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/utils';

.rating {
  opacity: 0.4;
  display: flex;
  flex-flow: row;
  align-items: center;

  .label {
    font-size: 0.8rem;
    margin-right: 0.75rem;
  }
}

img {
  @include pointer-on-hover();
}
</style>
