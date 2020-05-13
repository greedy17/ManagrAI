<template>
  <div class="note-action">
    <FormField :errors="notesForm.fc['title'].errors" binding="title" labelText="Note Title">
      <template v-slot:input>
        <input
          id="title"
          :name="notesForm.fc['title'].name"
          class="note-title"
          v-model="notesForm.fc['title'].value"
          placeholder="Note Title"
          @blur="notesForm.fc['title'].validate()"
        />
      </template>
    </FormField>
    <FormField :errors="notesForm.fc['content'].errors" binding="content" labelText="Note Content">
      <template v-slot:input>
        <textarea
          id="content"
          :name="notesForm.fc['content'].name"
          class="note-detail"
          v-model="notesForm.fc['content'].value"
          placeholder="Note Detail"
          @blur="notesForm.fc['content'].validate()"
        />
      </template>
    </FormField>
    <div class="save-button-container">
      <span @click="emitSaveNote" class="save-button">Save</span>
    </div>
  </div>
</template>

<script>
import Note from '@/services/notes'
import FormField from '@/components/forms/FormField'
import { FormGroup } from '@/services/forms/index'
import { required } from '@/services/forms/validators/index'
export default {
  name: 'NoteAction',
  components: { FormField },

  data() {
    return {
      // notify that item was successfully created and reset form

      note: new Note(),
      notesForm: new FormGroup({
        name: 'Note Form',
        fields: [
          {
            name: 'title',
            value: '',
            validators: [required({ message: 'Please Enter a Title for Your Note' })],
          },
          {
            name: 'content',
            value: '',
            validators: [required({ message: 'Please Enter Some Content for Your Note' })],
          },
        ],
      }),
    }
  },

  methods: {
    emitSaveNote() {
      this.notesForm.validate()
      if (!this.notesForm.valid) {
        return
      }

      this.$emit('save-note', this.notesForm.Value)
    },
  },
  created() {},
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

.save-button-container {
  display: flex;
  flex-flow: row;
}

.save-button {
  @include primary-button();
  margin-left: auto;
}
</style>
