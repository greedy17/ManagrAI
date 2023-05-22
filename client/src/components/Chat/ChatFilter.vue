<template>
  <div class="filter-container">
    <header>
      <p v-if="!selectedFilter">Select Filters</p>

      <div
        style="margin-left: -0.75rem"
        v-else
        @click="selectedFilter = null"
        class="flexed-row pointer"
      >
        <img src="@/assets/images/back.svg" height="16px;width:16px" alt="" />

        {{ selectedFilter.name }}
      </div>

      <p @click="toggleShowFilters">x</p>
    </header>

    <section v-if="!selectedFilter">
      <div
        @click="selectFilter(filter)"
        v-for="filter in filters"
        :key="filter.name"
        class="icon-row"
      >
        <font-awesome-icon :icon="`fa-solid  ${filter.icon}`" />
        <p>{{ filter.name }} <span></span></p>
      </div>

      <div v-if="activeFilters.length" class="active-filters">
        <div
          :title="af[1] + ' ' + af[0].toLowerCase() + ' ' + af[2]"
          v-for="(af, i) in activeFilters"
          :key="i"
        >
          <p>{{ af[1] + ' ' + af[0].toLowerCase() + ' ' + af[2] }}</p>

          <span @click="removeFilter(af)" class="remove">x</span>
        </div>
      </div>
    </section>

    <section v-else>
      <div>
        <Multiselect
          :placeholder="`${selectedFilter.name}`"
          style="width: 100%; font-size: 14px"
          v-model="selectedOperator"
          :options="operators"
          @select="selectOperator($event.value, $event.label)"
          openDirection="below"
          selectLabel=""
          track-by="value"
          label="label"
        >
          <template slot="noResult">
            <p class="multi-slot">No results.</p>
          </template>
        </Multiselect>

        <div v-if="selectedFilter.operator">
          <input
            class="filter-input"
            :placeholder="`${selectedFilter.name} ${selectedFilter.operatorLabel}`"
            :type="`${selectedFilter.dataType}`"
            v-model="selectedFilter.value"
            autofocus="true"
          />
        </div>

        <div style="margin: 1rem 0 1rem 0.25rem" v-if="selectedFilter.value">
          <p>
            <span style="color: #9596b4">Filter : </span>
            "{{ selectedFilter.name }} is {{ selectedFilter.operatorLabel }}
            {{ selectedFilter.value }}"
          </p>
        </div>

        <button
          @click="addFilter()"
          v-if="selectedFilter.name && selectedFilter.operator && selectedFilter.value"
          class="chat-button shimmer"
          style="padding: 0.5rem 1rem"
        >
          Add filter
        </button>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'ChatFilter',
}
</script>

<style lang="scss" scoped>
</style>