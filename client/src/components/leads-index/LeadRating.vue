<template>
  <div class="rating" :class="{ active: selected == rating }" @click="onRatingClick(rating)">
    <span v-for="n in 5" :key="n" class="icon-container">
      <span class="icon">
        <svg class="svg" :class="{ fill: n <= rating }" viewBox="0 0 30 30">
          <use xlink:href="@/assets/images/svg-repo.svg#star" />
        </svg>
      </span>
      <!--       <img v-if="n <= rating" src="@/assets/images/star.svg" alt="star filled" />
      <img v-else src="@/assets/images/star_outline.svg" alt="star outline" /> -->
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
    selected: {
      type: Number,
      default: null,
    },
    isActive: {
      type: Boolean,
    },
  },
  created() {},
  data() {
    return {
      ratingChange: '',
    }
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
@import '@/styles/variables';

.rating {
  @include pointer-on-hover();
  border: 2px solid rgba($color: $dark-green, $alpha: 0);

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
.icon {
  display: block;
  width: 20px;
  height: 20px;
}

.svg.fill {
  fill: rgba($color: $dark-green, $alpha: 1);
}

.active {
  border: solid 2px rgba($color: $dark-green, $alpha: 0.2);
}
</style>
