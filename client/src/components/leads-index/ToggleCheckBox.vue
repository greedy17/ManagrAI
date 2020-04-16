<template>
  <label class="toggle">
    <input type="checkbox" class="toggle" v-model="donationCart.tipEveryTime" />
    <div>
      <div></div>
    </div>
  </label>
</template>

<script>
export default {
  name: 'ToggleCheckBox',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

label.toggle {
  cursor: pointer;
  height: 3rem;
  width: 3rem;
  background-color: red;
}
input[type='checkbox'].toggle {
  display: none;
}
// Normal Track
input[type='checkbox'].toggle + div {
  vertical-align: middle;
  width: 40px;
  height: 20px;
  border-radius: 999px;
  background-color: $soft-gray;
  transition-duration: 0.4s;
  transition-property: background-color, box-shadow;
  box-shadow: inset 0 0 0 0px rgba(0, 0, 0, 0.4);
}
// Checked Track (Green)
input[type='checkbox'].toggle:checked + div {
  width: 40px;
  background-position: 0 0;
  background-color: $dark-green;
}
// Normal Knob
input[type='checkbox'].toggle + div > div {
  float: left;
  width: 18px;
  height: 18px;
  border-radius: inherit;
  background: #ffffff;
  transition-timing-function: cubic-bezier(0.54, 1.85, 0.5, 1);
  transition-duration: 0.4s;
  transition-property: transform, background-color, box-shadow;
  transition-timing-function: cubic-bezier(0.54, 1.85, 0.5, 1);
  transition-duration: 0.4s;
  transition-property: transform, background-color;
  pointer-events: none;
  margin-top: 1px;
  margin-left: 1px;
}
// Checked Knob (Blue Style)
input[type='checkbox'].toggle:checked + div > div {
  transform: translate3d(20px, 0, 0);
  transform: translate3d(20px, 0, 0);
  background-color: #ffffff;
}
</style>
