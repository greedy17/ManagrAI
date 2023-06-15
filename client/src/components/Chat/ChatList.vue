<template>
  <section class="lists">
    <header class="list-header">
      <p><span>List: </span> {{ currentView.title }}</p>
    </header>
    <section class="chat-table-section">
      <div class="table">
        <div class="table-row sticky-header">
          <div style="margin-left: 1rem" class="table-cell">Name</div>
          <div class="table-cell">Stage</div>
          <div class="table-cell">Close Date</div>
        </div>
        <div v-for="(opp, i) in currentView.sobjectInstances" :key="i" class="table-row">
          <div @click="setOpp(opp.Name)" class="table-cell ellipsis-text">
            <p class="gray-bg pointer">
              {{ opp.Name }}
            </p>
          </div>
          <div class="table-cell">
            <p>
              {{ opp.StageName }}
            </p>
          </div>
          <div class="table-cell">
            <p>
              {{ opp.CloseDate }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <div class="row">
      <button>
        <img class="gold-filter" src="@/assets/images/sparkle.svg" height="16px" alt="" />Ask Managr
      </button>
      <button>
        <img class="gold-filter" src="@/assets/images/sparkle.svg" height="16px" alt="" />Run Deal
        Review
      </button>
      <button>
        <img class="gold-filter" src="@/assets/images/sparkle.svg" height="16px" alt="" />Call
        Summary
      </button>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ChatList',
  components: {},
  props: {},
  data() {
    return {
      message: '',
    }
  },
  methods: {
    setOpp(name) {
      this.$emit('set-opp', name)
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    currentView() {
      return this.$store.state.currentView
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

button {
  @include chat-button();
  padding: 0.7rem 1rem;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  margin-right: 1rem;
  img {
    margin-right: 0.5rem;
  }
}

.sticky-header {
  position: sticky;
  top: 0;
  background-color: white;
  padding: 0.5rem 0;
  font-weight: 500;
  color: $light-gray-blue;
  font-size: 12px !important;
}

.gold-filter {
  filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(90%) contrast(87%);
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: white;
  padding: 1rem 0;
  padding-left: 1.25rem;
  margin-top: 1rem;
  width: 100%;
}

.lists {
  height: 100%;
  width: 100%;
  overflow-y: scroll;
  overflow-x: hidden;
}

.chat-table-section {
  height: 45vh;
  overflow: scroll;
  padding: 0 1.25rem;
  background-color: white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.chat-table-section::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.chat-table-section::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px !important;
}
.chat-table-section:hover::-webkit-scrollbar-thumb {
  background-color: $base-gray;
}

.table {
  display: grid;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  font-size: 14px;
}

.list-header {
  position: sticky;
  background-color: white;
  top: 0;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  p {
    font-size: 12px;
    padding: 0;
    margin: 0;
    span {
      color: $light-gray-blue;
      margin-right: 0.25rem;
    }
  }
}

.gray-bg {
  background-color: $off-white;
  border-radius: 5px;
  padding: 0.5rem 1rem;
}

.ellipsis-text {
  white-space: nowrap;
  overflow: hidden;
  width: fit-content;
  max-width: 200px;
  margin-top: -0.5rem;

  p {
    text-overflow: ellipsis;
  }
}

.table-cell {
  padding: 0.25rem 0;
}

.pointer {
  cursor: pointer;
  &:hover {
    opacity: 0.5;
  }
}

// .th {
//   display: table-cell;
//   line-height: 1;
//   z-index: 2;
//   font-weight: 900;
//   font-size: 14px;
//   color: $base-gray;
//   width: 300px;
// }

// .table-row {
//   display: table-row;
// }

// .chat-table {
//   display: table;
// }

// .cell {
//   line-height: 1;
//   display: table-cell;
//   padding-bottom: 0.5rem;

//   p {
//     font-size: 14px;
//     overflow: hidden;
//     white-space: nowrap;
//     width: 300px;
//   }
// }
</style>