<template>
  <div class="nav-link" :class="{ active: isCurrentRoute }" @click="handleClick">
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
      if (!this.isCurrentRoute) {
        this.$router.push({ name: this.to })
      }
    },
  },
  computed: {
    isCurrentRoute() {
      return this.$route.name === this.to
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
  height: 4.5rem;
  width: 5rem;
  display: inline-flex;
  flex-flow: column;
  justify-content: center;
  align-items: center;
  margin: 0 3%;
  border-bottom: 2px solid rgba($color: $dark-green, $alpha: 0);
}

.active {
  border-bottom: 2px solid $dark-green;
}

.icon {
  height: 1.5rem;
  width: 1.5rem;
}

.content {
  @include base-font-styles();
  font-size: 11px;
  line-height: 1.45;
  text-align: center;
  color: $main-font-gray;
}
</style>
