<template>
  <div class="note-action">
    <input class="note-title" placeholder="Title" />
    <textarea class="note-detail" placeholder="Detail" />
    <div class="save-button-container">
      <span class="save-button">Save</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NoteAction',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/inputs';

.note-action {
  width: 100%;
  display: flex;
  flex-flow: column;
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
