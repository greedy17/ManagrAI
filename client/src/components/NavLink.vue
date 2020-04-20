<template>
  <div class="nav-link" :style="activeStyles" @click="handleClick">
    <img alt="icon" :src="require(`@/assets/images/${icon}.svg`)" class="icon" />
    <span class="content">
      <slot />
    </span>
  </div>
</template>

<script>
export default {
  name: 'NavLink',
  props: {
    to: { type: String, required: true },
    icon: String,
  },
  methods: {
    handleClick() {
      // NOTE(Bruno 4-15-20): Reports is not built and so is made inactive
      if (!this.isCurrentRoute && this.to !== 'Reports') {
        this.$router.push({ name: this.to })
      }
    },
  },
  computed: {
    isCurrentRoute() {
      return this.$route.name === this.to
    },
    activeStyles() {
      return { borderBottom: this.isCurrentRoute ? '2px solid #2F9E54' : '2px solid #ffffff' }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.nav-link {
  @include disable-text-select();
  @include pointer-on-hover();
  height: 4rem;
  width: 3.6rem;
  display: flex;
  flex-flow: column;
  justify-content: center;
  align-items: center;
  margin: 0 3%;
}

.icon {
  height: 1.5rem;
  width: 1.5rem;
}

.content {
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 11px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  text-align: center;
  color: $main-font-gray;
}
</style>
