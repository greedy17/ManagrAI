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
  height: 40px;
  border-radius: 4px;
  background-color: #fafafa;
  border: none;
  box-sizing: border-box;
  padding: 3%;

  &:focus {
    box-shadow: 0 0 10px rgba($color: #199e54, $alpha: 0.5);
    outline: none;
    background-color: #ffffff;
  }

  &::placeholder {
    opacity: 0.5;
    font-family: 'Lato', sans-serif;
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
  background-color: #fafafa;
  font-family: 'Lato', sans-serif;
  font-size: 14px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: #444444;

  &:focus {
    box-shadow: 0 0 10px rgba($color: #199e54, $alpha: 0.5);
    outline: none;
    background-color: #ffffff;
  }

  &::placeholder {
    opacity: 0.5;
    font-family: 'Lato', sans-serif;
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
  background-color: #199e54;
  font-family: 'Lato', sans-serif;
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
