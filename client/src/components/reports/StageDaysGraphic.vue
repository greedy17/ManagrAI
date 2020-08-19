<template>
  <div class="container" :class="{ 'as-card': asCard }">
    <img class="icon" :src="require(`@/assets/images/${icon}.svg`)" />
    <div class="count">{{ count === null ? 'Skipped' : count }}</div>
    <div class="title">{{ titleTop }}</div>
    <div class="title">{{ titleBottom }}</div>
    <ProgressBar
      :percentComplete="(count / average) * 100"
      style="margin: 2rem 0 0.5rem 0 ;"
      v-if="progressBar"
    />
    <div class="average">Average: {{ average || 0 }}</div>
  </div>
</template>

<script>
import ProgressBar from '@/components/reports/ProgressBar'

export default {
  name: 'StageDaysGraphic',
  props: {
    icon: {
      type: String,
      required: true,
    },
    count: {
      required: true,
    },
    average: {
      required: true,
    },
    titleTop: {
      type: String,
      required: true,
    },
    titleBottom: {
      type: String,
      required: true,
    },
    progressBar: {
      type: Boolean,
      default: true,
    },
    asCard: {
      type: Boolean,
      default: true,
    },
  },
  components: {
    ProgressBar,
  },
  created() {},
  methods: {},
  watch: {},
  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/mixins/inputs';
@import '@/styles/forms';

.container {
  padding: 2rem 1rem 3rem 1rem;
  background-color: $white;
  border-radius: 0.5rem;
  margin: 0 1rem;
}

.as-card {
  box-shadow: 0 0 5px 1px $soft-gray;
}

.icon {
  height: 3rem;
}

.count {
  color: $dark-green;
  font-size: 2.5rem;
  margin-top: 0.2rem;
  margin-bottom: 1rem;
}

.title {
  font-size: 1.3rem;
  font-weight: 500;
}

.average {
  font-style: italic;
  color: $gray;
}
</style>
