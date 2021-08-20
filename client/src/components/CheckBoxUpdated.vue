<template>
  <div class="checkbox">
    <div v-if="checked" class="checkbox--filled" />
    <!-- <img v-else alt="empty" src="@/assets/images/check-box-empty.svg" /> -->
    <div v-else class="checkbox--empty" />
  </div>
</template>

<script>
export default {
  name: 'CheckBox',
  props: {
    checked: {
      type: Boolean,
      required: true,
    },
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/utils';

.checkbox {
  @include pointer-on-hover();
  height: 1.5rem;
  width: 1.5rem;
  img {
    height: 1.5rem;
    width: 1.5rem;
  }

  &--empty {
    width: 1rem;
    height: 1rem;
    background-color: #f4f5f6;
    margin-left: 0.2rem;
    margin-top: 0.3rem;
    border-radius: 0.15rem;
  }

  &--filled {
    width: 1rem;
    height: 1rem;
    background-color: $dark-green;
    margin-left: 0.2rem;
    margin-top: 0.3rem;
    border-radius: 0.15rem;
    border: 2px solid white;
  }
}
</style>
