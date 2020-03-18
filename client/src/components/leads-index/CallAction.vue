<template>
  <div class="call-action">
    <div class="call-action-left-pane">
      left-pane
    </div>
    <div class="call-action-right-pane">
      <div class="text-area-container">
        <textarea placeholder="Detail" />
      </div>
      <div class="save-button-container">
        <span class="save-button">Save</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CallAction',
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

.call-action {
  width: 100%;
  display: flex;
  flex-flow: row;
}

.call-action-left-pane {
  width: 45%;
}

.call-action-right-pane {
  flex-grow: 1;
  display: flex;
  flex-flow: column;
}

.text-area-container {
  height: 95%;
  display: flex;
  align-items: top;
  justify-content: center;
}

textarea {
  resize: none;
  height: 94%;
  width: 98%;
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

// div {
//   border: 1px dashed black;
// }
</style>
