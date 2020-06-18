<template>
  <div class="flexbox-container">
    <div class="flexbox-container__column">
      <div class="form">
        <div class="form__element">
          <div class="form__element-header">Type</div>
          <select class="form__select" v-model="type">
            <option disabled :value="null">Select Action Type</option>
            <option
              v-for="choice in actionChoices.list"
              :key="choice.id"
              :value="choice.id"
            >{{ choice.title }}</option>
          </select>
          <div
            class="form__element-error"
            v-if="isFormValid !== null && !isFormValid && errors.typeNotSelected"
          >Must select an Action Type.</div>
        </div>

        <div class="form__element">
          <div class="form__element-header">Description</div>
          <textarea v-model="description" class="form__textarea" />
          <div
            class="form__element-error"
            v-if="isFormValid !== null && !isFormValid && errors.descriptionIsBlank"
          >Must include a description.</div>
        </div>
      </div>
      <div class="form__element">
        <div class="form__element-header">Date</div>
        <input v-model="date" type="datetime-local" class="form__input" />
        <div
          class="form__element-error"
          v-if="isFormValid !== null && !isFormValid && errors.dateNotSelected"
        >Must select a date.</div>
      </div>
      <div class="form__element">
        <button class="form__button" @click.prevent="onBulkLogging">Save</button>
      </div>
    </div>
  </div>
</template>

<script>
import CollectionManager from '@/services/collectionManager'
import ActionChoice from '@/services/action-choices'
import Action from '@/services/actions'

export default {
  name: 'BulkCustomAction',
  props: {
    leads: {
      required: true,
      type: Array,
    },
  },
  data() {
    return {
      actionChoices: CollectionManager.create({
        ModelClass: ActionChoice,
        filters: {
          ordering: 'title',
        },
      }),
      type: null,
      description: '',
      date: null,
      isFormValid: null,
      errors: {},
    }
  },
  created() {
    this.actionChoices.refresh()
  },
  methods: {
    onBulkLogging() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data for this request
      let validationResults = this.clientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      let leads = this.leads.map(l => l.id)
      Action.api.bulkCreate(this.type, this.description, leads).then(() => {
        this.$Alert.alert({
          type: 'success',
          timeout: 4000,
          message: 'Action logged for selected leads!',
        })
        this.$parent.$emit('bulk-success')
      })
    },
    clientSideValidations() {
      let formErrors = {
        typeNotSelected: this.typeNotSelected,
        descriptionIsBlank: this.descriptionIsBlank,
        dateNotSelected: this.dateNotSelected,
      }
      let isFormValid = !this.typeNotSelected && !this.descriptionIsBlank && !this.dateNotSelected

      return [isFormValid, formErrors]
    },
  },
  computed: {
    typeNotSelected() {
      return !this.type
    },
    descriptionIsBlank() {
      return !this.description.length
    },
    dateNotSelected() {
      return !this.date
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/forms';
@import '@/styles/mixins/inputs';
</style>
