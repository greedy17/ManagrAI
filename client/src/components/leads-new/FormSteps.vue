<template>
  <div class="form-steps">
    <div class="header section-shadow">
      Add an Opportunity
    </div>
    <div class="step">
      <span class="title">Step 1</span>
      <div v-if="currentStep > 1" class="checkmark">
        <img class="icon" alt="checkmark" src="@/assets/images/checkmark.svg" />
      </div>
    </div>
    <div class="step">
      <span class="title">Step 2</span>
      <div v-if="currentStep > 2" class="checkmark">
        <img class="icon" alt="checkmark" src="@/assets/images/checkmark.svg" />
      </div>
    </div>
    <div class="step">
      <span class="title">Step 3</span>
      <div v-if="currentStep > 3" class="checkmark">
        <img class="icon" alt="checkmark" src="@/assets/images/checkmark.svg" />
      </div>
    </div>
    <div class="step">
      <span class="title">Edit + get to closing!</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FormSteps',
  props: {
    currentStep: {
      type: Number,
      required: true,
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.form-steps {
  @include standard-border();
  background-color: $white;
  height: 20rem;
  width: 17rem;
}

.header {
  @include base-font-styles();
  color: $main-font-gray;
  line-height: 1.14;
  font-size: 1rem;
  font-weight: bold;
  height: 3rem;
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.step {
  display: flex;
  flex-flow: row;
  height: 3rem;
  padding: 0 1rem;

  .title {
    width: 70%;
    display: flex;
    flex-flow: column;
    justify-content: center;
  }

  .checkmark {
    margin-left: auto;
    display: flex;
    flex-flow: column;
    justify-content: center;

    .icon {
      height: 1.5rem;
      width: 1.5rem;
    }
  }
}
</style>
