import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import database from './utils/database';

// Import routes
import pigeonsRouter from './routes/pigeons';
import racesRouter from './routes/races';
import dashboardRouter from './routes/dashboard';
import pairingsRouter from './routes/pairings';
import healthRouter from './routes/health';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 8001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Pigeon Racing Management System API',
    version: '2.0.0',
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

// API Routes
app.use('/api/pigeons', pigeonsRouter);
app.use('/api', racesRouter);
app.use('/api', dashboardRouter);
app.use('/api/pairings', pairingsRouter);
app.use('/api', healthRouter);

// Error handling middleware
app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    detail: 'Internal server error',
    message: error.message || 'Unknown error occurred'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    detail: 'Endpoint not found',
    path: req.originalUrl,
    method: req.method
  });
});

// Database connection and server startup
async function startServer() {
  try {
    // Connect to database
    await database.connect();
    
    // Start server
    app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 Server running on http://0.0.0.0:${PORT}`);
      console.log(`📊 API Documentation available at http://0.0.0.0:${PORT}/api`);
      console.log(`🐦 Pigeon Racing Management System v2.0.0`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down server...');
  await database.disconnect();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Shutting down server...');
  await database.disconnect();
  process.exit(0);
});

// Start the server
startServer();

export default app;