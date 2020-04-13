<template>
  <div class="reminder-action">
    <div class="reminder-title-date-container">
      <input class="reminder-title" placeholder="Title" />
      <input class="reminder-date" placeholder="Select Date" disabled />
    </div>
    <textarea class="reminder-detail" placeholder="Detail" />
    <div class="save-button-container">
      <span class="save-button">Save</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReminderAction',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/inputs';

.reminder-action {
  width: 100%;
  display: flex;
  flex-flow: column;
}

.reminder-title-date-container {
  display: flex;
  flex-flow: row;
}

.reminder-title {
  width: 46%;
}

.reminder-date {
  width: 49%;
  margin-left: 5%;
}

input {
  @include input-field();
  height: 40px;
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
