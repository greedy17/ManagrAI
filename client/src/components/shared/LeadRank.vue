<template>
  <div class="rank">
    <span v-if="label" class="label">Rank</span>
    <span v-for="(bool, index) in iconArray" :key="index" class="icon-container">
      <img v-if="bool" src="@/assets/images/star.svg" alt="star icon" />
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
  computed: {
    iconArray() {
      let arr = []
      for (let n = 1; n <= 5; ++n) {
        if (n <= this.rank) {
          arr.push(true)
        } else {
          arr.push(false)
        }
      }
      return arr
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
    margin-right: 12px;
  }
}
</style>
