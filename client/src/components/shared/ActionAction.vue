<template>
  <div class="action-action">
    <div class="action-type-date-container">
      <input class="action-type" placeholder="Action Type" disabled />
      <input class="action-date" placeholder="Select Date" disabled />
    </div>
    <textarea class="action-detail" placeholder="Detail" />
    <div class="save-button-container">
      <span class="save-button">Save</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActionAction',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/inputs';

.action-action {
  width: 100%;
  display: flex;
  flex-flow: column;
}

.action-type-date-container {
  display: flex;
  flex-flow: row;
}

.action-type {
  width: 46%;
}

.action-date {
  width: 49%;
  margin-left: 5%;
}

input {
  @include input-field();
  height: 2.5rem;
}

textarea {
  @include input-field();
  resize: none;
  height: 94%;
  flex-grow: 1;
  margin: 2% 0;
  font-size: 14px;
}

.save-button-container {
  display: flex;
  flex-flow: row;
}

.save-button {
  @include primary-button();
  margin-left: auto;
}
</style>
