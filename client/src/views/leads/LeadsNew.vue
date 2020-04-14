<template>
  <div class="leads-new">
    <NavBar />
    <div class="page-content">
      <div class="steps-pane">
        <FormSteps :currentStep="currentStep" />
      </div>
      <div class="form-pane">
        <Form :currentStep="currentStep" @clicked-next="showForm2" />
      </div>
    </div>
  </div>
</template>

<script>
import FormSteps from '@/components/leads-new/FormSteps'
import Form from '@/components/leads-new/Form'

// import CollectionManager from '@/services/collectionManager'

export default {
  name: 'LeadsNew',
  components: { FormSteps, Form },
  data() {
    return {
      accounts: null,
      currentStep: 1,
    }
  },
  methods: {
    showForm2() {
      this.currentStep = 2
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.leads-new {
  min-height: 100vh;
  display: flex;
  flex-flow: column;
  background-color: $off-white;
}

.page-content {
  padding-top: 2%;
  flex-grow: 1;
  display: flex;
  flex-flow: row;
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
