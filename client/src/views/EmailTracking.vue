<template>
  <div class="tracking">
    <h2>Track your outreach</h2>

    <section class="space-between">
      <div class="row">
        <div>
          <button class="secondary-button">Select User</button>
        </div>

        <div class="relative">
          <button @click="toggleFilterDropdown" class="primary-button">
            <img src="@/assets/images/add.svg" height="12px" alt="" /> Add Filter
          </button>
          <div v-if="showFilters" class="dropdown">
            <div class="dropdown-header">
              <h3>Filters</h3>
              <img
                @click="toggleFilterDropdown"
                src="@/assets/images/close.svg"
                class="pointer"
                height="18px"
                alt=""
              />
            </div>

            <div class="dropdown-body">
              <p>Status</p>
              <p>Last Activity</p>
              <p>Journalist</p>
            </div>

            <div class="dropdown-footer">
              <button class="primary-button">Apply</button>
            </div>
          </div>
        </div>
      </div>

      <div class="search">
        <div class="input">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
              fill="currentColor"
            ></path>
          </svg>
          <input v-model="searchEmailText" class="search-input" :placeholder="`Search...`" />
          <img
            v-if="searchEmailText"
            @click="clearSearchText"
            src="@/assets/images/close.svg"
            class="pointer"
            height="12px"
            alt=""
          />
        </div>
      </div>
    </section>

    <div class="table-container">
      <EmailTable :searchText="searchEmailText" />
    </div>
  </div>
</template>

<script>
import EmailTable from '../components/EmailTable.vue'

export default {
  name: 'EmailTracking',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    EmailTable,
  },
  data() {
    return {
      searchEmailText: '',
      showFilters: false,
    }
  },
  computed: {},
  mounted() {},

  methods: {
    clearSearchText() {
      this.searchEmailText = ''
    },
    toggleFilterDropdown() {
      this.showFilters = !this.showFilters
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.tracking {
  width: 100vw;
  height: 80vh;
  margin: 0 auto;
  padding: 72px 32px 16px 32px;
  font-family: $thin-font-family;
}

.table-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  margin-top: 24px;
  height: 100%;
  background-color: white;
  //   padding-top: 2px;
  overflow: scroll;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.primary-button {
  @include dark-blue-button();
  border: none;
  border-radius: 16px;

  img {
    filter: invert(100%);
    margin-right: 4px;
  }
}

.secondary-button {
  @include dark-blue-button();
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  border-radius: 16px;
}

.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.input {
  position: sticky;
  z-index: 2005;
  top: 1.5rem;
  width: 300px;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 10px 20px 10px 10px;
}

.search-input {
  border: none;
  outline: none;
  margin-left: 0.5rem;
  width: 100%;
}

.pointer {
  cursor: pointer;
}

.relative {
  position: relative;
}
.dropdown {
  position: absolute;
  top: 40px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 8px;
  left: 16px;
  z-index: 6;
  min-width: 25vw;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);

  .dropdown-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    img {
      margin-right: 8px;
    }
  }

  .dropdown-body {
  }
  .dropdown-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 8px;
  }
}
</style>
