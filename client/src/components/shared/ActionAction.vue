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
  height: 40px;
  border-radius: 4px;
  background-color: #fafafa;
  border: none;
  box-sizing: border-box;
  padding: 3%;

  &:focus {
    box-shadow: 0 0 10px rgba($color: $dark-green, $alpha: 0.5);
    outline: none;
    background-color: #ffffff;
  }

  &::placeholder {
    opacity: 0.5;
    font-family: $base-font-family, $backup-base-font-family;
    font-size: 14px;
    font-weight: normal;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.29;
    letter-spacing: 0.5px;
    color: #444444;
  }
}

textarea {
  resize: none;
  height: 94%;
  flex-grow: 1; //
  margin: 2% 0;
  box-sizing: border-box;
  padding: 3%;
  border-radius: 4px;
  border: none;
  background-color: $off-white;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: #444444;

  &:focus {
    box-shadow: 0 0 10px rgba($color: $dark-green, $alpha: 0.5);
    outline: none;
    background-color: #ffffff;
  }

  &::placeholder {
    opacity: 0.5;
    font-family: $base-font-family, $backup-base-font-family;
    font-size: 14px;
    font-weight: normal;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.29;
    letter-spacing: 0.5px;
    color: #444444;
  }
}

.save-button-container {
  display: flex;
  flex-flow: row;
}

.save-button {
  margin-left: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 15px;
  border-radius: 5px;
  background-color: $dark-green;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #ffffff;

  &:hover {
    cursor: pointer;
  }
}
</style>
