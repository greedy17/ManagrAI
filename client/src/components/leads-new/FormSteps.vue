<template>
  <div class="form-steps">
    <div class="header section-shadow">
      Add a Lead
    </div>
    <div class="step">
      <span class="title">Step 1</span>
      <div class="checkmark">
        <img class="icon" alt="checkmark" src="@/assets/images/checkmark.svg" />
      </div>
    </div>
    <div class="step">
      <span class="title">Step 2</span>
      <div class="checkmark">
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
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.form-steps {
  background-color: $white;
  height: 15rem;
  width: 15rem;
}

.header {
  font-family: $base-font-family, $backup-base-font-family;
  color: $main-font-gray;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  line-height: 1.14;
  font-size: 14px;
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

.section-shadow {
  box-shadow: 0 1px 0 0 $soft-gray;
}
</style>
