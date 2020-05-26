<template>
  <div class="reminder-action">
    <div class="reminder-title-date-container">
      <FormField
        :errors="remindersForm.fc['title'].errors"
        binding="title"
        labelText="Reminder Title"
      >
        <template v-slot:input>
          <input
            id="title"
            :name="remindersForm.fc['title'].name"
            class="reminder-title"
            v-model="remindersForm.fc['title'].value"
            placeholder="Reminder Title"
            @blur="remindersForm.fc['title'].validate()"
          />
        </template>
      </FormField>

      <FormField
        :errors="remindersForm.fc['datetimeFor'].errors"
        binding="datetimeFor"
        labelText="Reminder On"
      >
        <template v-slot:input>
          <datetime
            placeholder="Enter a date to be reminded on"
            :name="remindersForm.fc['datetimeFor'].name"
            id="datetimeFor"
            v-model="remindersForm.fc['datetimeFor'].value"
            @close="remindersForm.fc['datetimeFor'].validate()"
            class="reminder-detail"
          />
        </template>
      </FormField>
    </div>
    <FormField
      :errors="remindersForm.fc['content'].errors"
      binding="content"
      labelText="Reminder Content"
    >
      <template v-slot:input>
        <textarea
          id="content"
          :name="remindersForm.fc['content'].name"
          class="reminder-detail"
          v-model="remindersForm.fc['content'].value"
          placeholder="Reminder Content"
          @blur="remindersForm.fc['content'].validate()"
        />
      </template>
    </FormField>
    <div class="save-button-container">
      <span @click="emitSaveReminder" class="save-button">Save</span>
    </div>
  </div>
</template>

<script>
import Reminder from '@/services/reminders'
import FormField from '@/components/forms/FormField'
import { FormGroup } from '@/services/forms/index'
import { required } from '@/services/forms/validators/index'
export default {
  name: 'ReminderAction',
  components: { FormField },
  data() {
    return {
      reminder: new Reminder(),
      remindersForm: new FormGroup({
        name: 'Note Form',
        fields: [
          {
            name: 'title',
            value: '',
            validators: [required({ message: 'Please Enter a Title for Your Reminder' })],
          },
          {
            name: 'datetimeFor',
            value: '',
            validators: [],
          },
          {
            name: 'content',
            value: '',
            validators: [required({ message: 'Please Enter Some Content for Your Reminder' })],
          },
        ],
      }),
    }
  },

  methods: {
    openDateTimePicker(e) {
      console.log(e)
      console.log(this.$refs['datetime-picker'].open(e))
      console.log(Object.keys(this.$refs['datetime-picker']))
    },
    emitSaveReminder() {
      this.remindersForm.validate()
      if (!this.remindersForm.valid) {
        return
      }

      this.$emit('save-reminder', this.remindersForm.Value)
    },
  },
  created() {},
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
.datetime-picker-style {
  @include input-field();
  cursor: text;
  &::-webkit-input-placeholder {
    opacity: 0;
    transition: inherit;
    font-size: 14px;
    line-height: 1.29;
    letter-spacing: 0.5px;
    color: $base-gray;
    @include base-font-styles();
  }
}
.reminder-date {
  width: 49%;
  margin-left: 5%;
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
