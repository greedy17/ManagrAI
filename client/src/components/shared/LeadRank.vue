<template>
  <div class="rank">
    <span v-if="label" class="label">Rank</span>
    <span v-for="n in 5" :key="n" class="icon-container">
      <img v-if="n <= rank" src="@/assets/images/star.svg" alt="star icon" />
      <img v-else src="@/assets/images/star_outline.svg" alt="star outline icon" />
    </span>
  </div>
</template>

<script>
export default {
  name: 'LeadRank',
  props: {
    rank: {
      type: Number,
      required: true,
    },
    label: {
      type: Boolean,
    },
  },
}
</script>

<style lang="scss" scoped>
.rank {
  opacity: 0.4;
  display: flex;
  flex-flow: row;
  align-items: center;

  .label {
    font-size: 0.8rem;
    margin-right: 0.75rem;
  }
}
</style>
