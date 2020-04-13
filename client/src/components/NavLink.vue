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
      // NOTE: currently only for Leads link
      if (this.to === 'LeadsIndex' && !this.isCurrentRoute) {
        this.$router.push({ name: this.to })
      }
    },
  },
  computed: {
    isCurrentRoute() {
      return this.$route.name === this.to
    },
    activeStyles() {
      return this.isCurrentRoute
        ? { borderBottom: '2px solid #2F9E54' }
        : { borderBottom: '2px solid #ffffff' }
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
  height: 63px;
  width: 57px;
  display: flex;
  flex-flow: column;
  justify-content: center;
  align-items: center;
  margin: 0 3%;
}

.icon {
  height: 24px;
  width: 24px;
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
