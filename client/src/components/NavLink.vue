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
    active: Boolean,
    icon: String,
  },
  methods: {
    handleClick() {
      if (this.icon === 'leads') {
        this.$router.push('/leads')
      }
    },
  },
  computed: {
    activeStyles() {
      return this.active
        ? { borderBottom: '2px solid #2F9E54' }
        : { borderBottom: '2px solid #ffffff' }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.nav-link {
  height: 63px;
  width: 57px;
  display: flex;
  flex-flow: column;
  justify-content: center;
  align-items: center;
  margin: 0 3%;
  &:hover {
    cursor: pointer;
  }
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
