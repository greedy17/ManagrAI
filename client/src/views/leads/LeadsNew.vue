<template>
  <div class="leads-new">
    <NavBar />
    <div class="page-content">
      <div class="steps-pane">
        <FormSteps />
      </div>
      <div class="forms-pane">
        forms
      </div>
    </div>
  </div>
</template>

<script>
import FormSteps from '@/components/leads-new/FormSteps'

export default {
  name: 'LeadsNew',
  components: { FormSteps },
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

.forms-pane {
  width: 75vw;
}

div {
  border: 1px dashed black;
}
</style>
