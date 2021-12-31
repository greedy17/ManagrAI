<template>
  <div class="aa-notification" :class="alert.type" @click="$emit('remove', alert)">
    <img class="check" src="@/assets/images/check.png" alt="" />
    <div class="content" v-html="alert.message" />
    <img class="icon" alt="icon" src="@/assets/images/remove.svg" />
  </div>
</template>

<script>
export default {
  name: 'AlertAlertItem',
  props: ['alert'],
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.aa-notification {
  @include pointer-on-hover();
  width: 30vw;
  min-height: 4rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 0.5rem;
  transition: all 200ms ease-in-out;
  display: flex;
  align-items: center;
  flex-flow: row;
}

.aa-notification.info {
  background-color: rgba($color: $dark-gray-blue, $alpha: 0.9);
  border: 1px solid rgba($color: $dark-gray-blue, $alpha: 1.2);
  color: $white;
}

.aa-notification.success {
  background-color: rgba($color: $dark-green, $alpha: 1.5);
  border: 1px solid rgba($color: $dark-green, $alpha: 1.2);
  color: white;
  font-weight: bold;
}

.aa-notification.banner {
  background-color: rgba($color: $dark-green, $alpha: 0.4);
  border: 1px solid rgba($color: $dark-green, $alpha: 1);
  color: $main-font-gray;
}

.aa-notification.warning {
  background-color: rgba($color: $yellow, $alpha: 0.9);
  border: 1px solid rgba($color: $yellow, $alpha: 1.2);
  color: $main-font-gray;
}

.aa-notification.error {
  background-color: rgba($color: $coral, $alpha: 0.9);
  border: 1px solid rgba($color: $coral, $alpha: 1.2);
  color: white;
  font-weight: bold;
}

.content {
  flex-grow: 1;
}

.icon {
  margin-left: 0.75rem;
  height: 1.2rem;
  filter: invert(100%);
}
.check {
  height: 1rem;
  margin-right: 0.2rem;
}
</style>
