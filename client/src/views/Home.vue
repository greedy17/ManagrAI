<template>
  <div class="home">
    <div class="heading">
      <h3>Hi {{ user.firstName }}</h3>
      <p>Today is Tuesday, August 23, 2022</p>
    </div>

    <section class="command-center">
      <div class="command-center__section">
        <div>
          <p>Meetings <span>3</span></p>
          <div>
            <img src="@/assets/images/calendar.svg" height="16px" alt="" />
            <img src="@/assets/images/refresh.svg" height="20px" alt="" />
          </div>
        </div>
        <section></section>
      </div>

      <div class="command-center__section-pipeline">
        <div>
          <p>Pipeline <span>3</span></p>
          <div>
            <img src="@/assets/images/list.svg" height="16px" alt="" />
            <img src="@/assets/images/plusOne.svg" height="24px" alt="" />
          </div>
        </div>
        <section></section>
      </div>

      <div class="command-center__section-activity">
        <div>
          <p>Activity</p>
          <img src="@/assets/images/settings.svg" height="20px" alt="" />
        </div>
        <section></section>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      user: this.$store.state.user,
    }
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.home {
  margin-left: 88px;
}
.heading {
  h3 {
    margin-bottom: 0;
    font-size: 24px;
  }
  p {
    font-size: 13px;
    color: $light-gray-blue;
  }
}

.command-center {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;

  &__section {
    width: 24vw;
    div {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;

      p {
        font-size: 13px;
        span {
          background-color: $yellow;
          color: white;
          padding: 4px 8px;
          border-radius: 6px;
          margin-left: 4px;
        }
      }

      div {
        img {
          margin-left: 12px;
        }
      }
    }
  }

  &__section-pipeline {
    width: 40vw;
    div {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;

      p {
        font-size: 13px;
        span {
          background-color: $base-gray;
          color: white;
          padding: 4px 8px;
          border-radius: 6px;
          margin-left: 4px;
        }
      }

      div {
        img {
          margin-left: 12px;
        }
      }
    }
  }

  &__section-activity {
    width: 22vw;
    div {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;

      p {
        font-size: 14px;
      }

      div {
        img {
          margin-left: 12px;
        }
      }
    }
  }

  section {
    width: 100%;
    outline: 1px solid $soft-gray;
    height: 100%;
    margin-top: 16px;
    min-height: 70vh;
    border-radius: 4px;
    background-color: white;
    box-shadow: 1px 1px 2px 1px $very-light-gray;
  }
}
</style>