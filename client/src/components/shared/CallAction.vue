<template>
  <div class="call-action">
    <div class="call-action-left-pane">
      <div class="contacts-container">
        <div class="contact">
          <img class="contact-img" src="@/assets/images/sara-smith.png" alt="contact image" />
          <span class="contact-name">Sara Smith</span>
          <div class="contact-phone-number-container">
            <img class="telephone-icon" src="@/assets/images/telephone.svg" alt="icon" />
            <span class="contact-phone-number">555-555-5555</span>
          </div>
        </div>
        <div class="contact">
          <img class="contact-img" src="@/assets/images/jake-murray.png" alt="contact image" />
          <span class="contact-name">Jake Murray</span>
          <div class="contact-phone-number-container">
            <img class="telephone-icon" src="@/assets/images/telephone.svg" alt="icon" />
            <span class="contact-phone-number">555-555-5555</span>
          </div>
        </div>
      </div>
      <div class="details-container">
        <FormField
          :errors="callNotesForm.fc['title'].errors"
          binding="title"
          labelText="Call Note Title"
        >
          <template v-slot:input>
            <input
              id="title"
              :name="callNotesForm.fc['title'].name"
              class="call-note-title"
              v-model="callNotesForm.fc['title'].value"
              placeholder="Reminder Title"
              @blur="callNotesForm.fc['title'].validate()"
            />
          </template>
        </FormField>

        <FormField
          :errors="callNotesForm.fc['callDate'].errors"
          binding="callDate"
          labelText="Call Date"
        >
          <template v-slot:input>
            <datetime
              placeholder="Enter the date of the call"
              :name="callNotesForm.fc['callDate'].name"
              id="callDate"
              v-model="callNotesForm.fc['callDate'].value"
              @close="callNotesForm.fc['callDate'].validate()"
              class="call-note-detail"
            />
          </template>
        </FormField>
      </div>
    </div>
    <div class="call-action-right-pane">
      <div class="text-area-container">
        <FormField
          :errors="callNotesForm.fc['content'].errors"
          binding="content"
          labelText="Content"
        >
          <template v-slot:input>
            <textarea
              id="content"
              :name="callNotesForm.fc['content'].name"
              class="details-container"
              v-model="callNotesForm.fc['content'].value"
              placeholder="Content"
              @blur="callNotesForm.fc['content'].validate()"
            />
          </template>
        </FormField>
      </div>
      <div class="save-button-container">
        <span @click="emitSaveCallNote" class="save-button">Save</span>
      </div>
    </div>
  </div>
</template>

<script>
import CallNote from '@/services/call-notes'
import FormField from '@/components/forms/FormField'
import { FormGroup } from '@/services/forms/index'
import { required } from '@/services/forms/validators/index'
export default {
  name: 'CallAction',
  components: { FormField },
  data() {
    return {
      callNote: new CallNote(),
      callNotesForm: new FormGroup({
        name: 'Call Note Form',
        fields: [
          {
            name: 'title',
            value: '',
            validators: [required({ message: 'Please Enter a Title for Your Call Note' })],
          },
          {
            name: 'callDate',
            value: '',
            validators: [required({ message: 'Please Enter a Date  for Your Call Note' })],
          },
          {
            name: 'content',
            value: '',
            validators: [required({ message: 'Please Enter Some Content for Your Call Note' })],
          },
        ],
      }),
    }
  },

  methods: {
    emitSaveCallNote() {
      this.callNotesForm.validate()
      if (!this.callNotesForm.valid) {
        return
      }

      this.$emit('save-call-note', this.callNotesForm.Value)
    },
  },
  computed: {
    date() {
      let today = new Date()
      let dd = String(today.getDate()).padStart(2, '0')
      let mm = String(today.getMonth() + 1).padStart(2, '0') //January is 0!
      let yyyy = today.getFullYear()
      return mm + '/' + dd + '/' + yyyy
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/utils';

.call-action {
  width: 100%;
  display: flex;
  flex-flow: row;
}

/* left pane below */
.call-action-left-pane {
  width: 40%;
  padding-right: 3%;
  display: flex;
  flex-flow: column;
}

.contacts-container {
  display: flex;
  flex-flow: column;
}

.contact {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-bottom: 2%;
}

.contact-img {
  height: 1.5rem;
  width: 1.5rem;
  border-radius: 50%;
}

.contact-name {
  @include base-font-styles();
  margin-left: auto;
  width: 25%;
  font-size: 11px;
  line-height: 1.45;
  color: $main-font-gray;
}

.contact-phone-number-container {
  @include pointer-on-hover();
  width: 50%;
  height: 1.5rem;
  padding: 0.125rem;
  margin-left: auto;
  background-color: $soft-gray;
  border-radius: 5px;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.telephone-icon {
  height: 1rem;
  width: 1rem;
  margin-left: 0.375rem;
}

.contact-phone-number {
  @include base-font-styles();
  margin-left: 0.375rem;
  font-size: 11px;
  font-weight: bold;
  line-height: 1.45;
  color: $main-font-gray;
}

.details-container {
  margin-top: 3%;
  display: flex;
  flex-flow: column;
}

/* right-pane below */
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

.save-button-container {
  display: flex;
  flex-flow: row;
}

.save-button {
  @include primary-button();
  margin-left: auto;
}
</style>
