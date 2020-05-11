<template>
  <div class="aa-notification" :class="alert.type" @click="$emit('remove', alert)">
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
  width: 96vw;
  min-height: 1.5rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 3px;
  transition: all 200ms ease-in-out;
  display: flex;
  flex-flow: row;
}

.aa-notification.info {
  background-color: rgba($color: $dark-gray-blue, $alpha: 0.9);
  border: 1px solid rgba($color: $dark-gray-blue, $alpha: 1.2);
  color: $white;
}

.aa-notification.success {
  background-color: rgba($color: $lime-green, $alpha: 0.9);
  border: 1px solid rgba($color: $lime-green, $alpha: 1.2);
  color: $main-font-gray;
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
  color: $main-font-gray;
}

.content {
  flex-grow: 1;
}

.icon {
  margin-left: 0.75rem;
  height: 1.2rem;
}
</style>
