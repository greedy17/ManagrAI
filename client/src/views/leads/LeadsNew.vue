<template>
  <div class="leads-new">
    <div class="steps-pane">
      <FormSteps :currentStep="currentStep" />
    </div>
    <div class="form-pane">
      <Form
        :currentStep="currentStep"
        @to-create-account="toCreateAccount"
        @to-add-contacts="toAddContacts"
      />
    </div>
  </div>
</template>

<script>
import FormSteps from '@/components/leads-new/FormSteps'
import Form from '@/components/leads-new/Form'

export default {
  name: 'LeadsNew',
  components: { FormSteps, Form },
  data() {
    return {
      currentStep: 1,
    }
  },
  methods: {
    toCreateAccount() {
      this.currentStep = 2
    },
    toAddContacts() {
      this.currentStep = 3
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.leads-new {
  display: flex;
  flex-flow: row;
  padding-top: 2%;
}

.steps-pane {
  width: 25vw;
  display: flex;
  flex-flow: column;
  align-items: center;
}

.form-pane {
  width: 75vw;
}
</style>
