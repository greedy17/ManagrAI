<template>
  <div class="aa-notification" :class="alert.type" @click="$emit('remove', alert)">
    <div class="row">
      <img class="check" src="@/assets/images/check.png" alt="" />
      <div class="col">
        <div class="content" v-html="alert.message" />
        <div class="subs" v-html="alert.sub" />
      </div>
    </div>

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
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  min-width: 24vw;
  max-width: 30vw;
  min-height: 4.5rem;
  padding: 0.5rem;
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
  background-color: white;
  border: white;
  border-radius: 0.33rem;
  color: $base-gray;
  font-weight: bold;
  box-shadow: 1px 2px 7px $very-light-gray;
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
  font-size: 18px;
}
.subs {
  font-size: 12px;
  color: $very-light-gray;
}
.col {
  display: flex;
  flex-direction: column;
}
.row {
  display: flex;
  align-items: center;
  flex-direction: row;
  height: 100%;
  border-radius: 0.1rem;
  padding-left: 0.5rem;
}
.icon {
  margin-left: 0.75rem;
  height: 1.25rem;
  width: 1.5rem;
  filter: invert(60%);
  align-self: flex-start;
  padding: 0.1rem;
}
.check {
  height: 1.25rem;
  margin-right: 0.75rem;
  filter: invert(46%) sepia(20%) saturate(1576%) hue-rotate(94deg) brightness(102%) contrast(92%);
}
</style>
