<template>
  <div>
    <line-chart :chart-data="chartData" :options="chartOptions"></line-chart>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart, registerables } from 'chart.js'

// Register Chart.js components
Chart.register(...registerables)

export default {
  name: 'LineChartComponent',
  components: {
    LineChart: {
      extends: Line,
      props: ['chartData', 'options'],
      mounted() {
        this.renderChart(this.chartData, this.options)
      },
      watch: {
        chartData: {
          handler(newData) {
            this.renderChart(newData, this.options)
          },
          deep: true,
        },
        options: {
          handler(newOptions) {
            this.renderChart(this.chartData, newOptions)
          },
          deep: true,
        },
      },
    },
  },
  data() {
    return {
      chartData: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [
          {
            label: 'Sales',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            pointBackgroundColor: 'rgba(54, 162, 235, 1)',
            data: [30, 50, 40, 60, 70, 90, 100],
            fill: true,
            tension: 0.4,
          },
        ],
      },
      chartOptions: {
        responsive: true,
        plugins: {
          legend: {
            display: true,
            position: 'top',
          },
          tooltip: {
            enabled: true,
            mode: 'index',
            intersect: false,
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
          },
          y: {
            ticks: {
              beginAtZero: true,
            },
            grid: {
              display: true,
              color: 'rgba(200, 200, 200, 0.3)',
            },
          },
        },
      },
    }
  },
}
</script>

<style scoped>
div {
  max-width: 800px;
  margin: auto;
}
</style>
